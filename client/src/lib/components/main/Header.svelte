<script lang="ts">
  import { Navbar, NavBrand, NavLi, NavUl, NavHamburger, Avatar, Dropdown, DropdownItem, DropdownHeader, DropdownGroup } from "flowbite-svelte";
</script>

<Navbar class="bg-header-gradient py-0">
    <NavBrand href="/">
        <img src="/spotly-logo-color.svg" class="me-3 h-6 sm:h-9" alt="Spotly Logo" />
        <span class="self-center text-xl text-white font-semibold whitespace-nowrap dark:text-foreground">SPOTLY</span>
    </NavBrand>
    <Dropdown placement="bottom" triggeredBy="#avatar-menu">
        <DropdownHeader>
            <span class="block text-sm">Pepe Pelotas</span>
            <span class="block truncate text-sm font-medium">pepe@pelotas.com</span>
        </DropdownHeader>
        <DropdownGroup>
            <DropdownItem class="cursor-pointer">Settings</DropdownItem>
            <DropdownItem class="cursor-pointer">Status</DropdownItem>
        </DropdownGroup>
        <DropdownHeader class="cursor-pointer">Sign out</DropdownHeader>
    </Dropdown>
    <NavUl class="text-white ">
        <NavLi href="/dashboard" class="text-inherit hover:text-accent">Dashboard</NavLi>
        <NavLi href="/status" class="text-inherit hover:text-accent">Status</NavLi>
    </NavUl>
    <div class="flex items-center md:order-2 cursor-pointer">
        <Avatar id="avatar-menu" src="/abstract-user-flat-4.svg" class="max-w-[40px] my-2" />
        <NavHamburger class="cursor-pointer"/>
    </div>
</Navbar>
